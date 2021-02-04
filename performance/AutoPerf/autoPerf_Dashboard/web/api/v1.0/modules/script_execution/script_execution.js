const config = require('../../../../config');
const statusCode = require('../../../../common/statusCode');
const exec = require('child_process').exec;
const execSync = require('child_process').execSync;
const propertiesReader = require('properties-reader');
const fs = require('fs');
const { info } = require('console');
const db = require(`../script_execution/database/${config.database}/${config.database}`);

class ScriptExecutionService {

    async getAllScriptExecutionsByUserGID(user_gid) {
        try {
            const scriptExecLogs = await db.scriptExecutionDatabase().getAllScriptExecutionsByUserGID(user_gid);
            return {
                statusCode: statusCode.success,
                message: "All script logs",
                data: scriptExecLogs
            };
        } catch (error) {
            throw {
                statusCode: error.statusCode,
                message: error.message,
                data: JSON.stringify(error)
            };
        }
    }

    async getScriptExecutionById(id) {
        try {
            const scriptExecLog = await db.scriptExecutionDatabase().getScriptExecutionById(id);
            return {
                statusCode: statusCode.success,
                message: "Script log by id",
                data: scriptExecLog
            };
        } catch (error) {
            throw {
                statusCode: error.statusCode,
                message: error.message,
                data: JSON.stringify(error)
            };
        }
    }

    async createScriptExecution(user_gid, script_args) {
        let cmdString = config.s3_workloads_script + ' ' + script_args.benchmark + ' ' + script_args.configuration + ' ' + script_args.client + ' ' + script_args.primary_server + ' ' + script_args.secondary_server + ' ' + script_args.sampling;
        if (script_args.benchmark === 'cosbench') {
            cmdString = cmdString + ' ' + script_args.operation;
        }
        if (script_args.benchmark === 'fio') {
            cmdString = cmdString + ' ' + script_args.template;
        }

        try {
            const scriptExec = {
                user_gid: user_gid,
                log: ">>> " + cmdString + "\n",
                start_time: new Date().getTime()
            };
            const scriptExecObj = await db.scriptExecutionDatabase().createScriptExecution(scriptExec);
            // await setClientServer(args, stream);
            const childProcess = exec(cmdString);
            childProcess.stdout.on('data', async (data) => {
                await db.scriptExecutionDatabase().updateScriptExecution(scriptExecObj._id, data.toString());
            });
            childProcess.stderr.on('data', async (data) => {
                await db.scriptExecutionDatabase().updateScriptExecution(scriptExecObj._id, data.toString());
            });
            childProcess.on('close', async (code) => {
                const log = "\nScript execution terminated with code: " + code;
                await db.scriptExecutionDatabase().updateScriptExecution(scriptExecObj._id, log, true);
            });
            return {
                statusCode: statusCode.created,
                message: "Command execution started successfully."
            };
        } catch (error) {
            throw {
                statusCode: error.statusCode,
                message: error.message,
                data: JSON.stringify(error),
            };
        };        
    }

    async setClientServer(args, logFileStream) {
        const properties = propertiesReader(config.launch_benchmark_conf_file);
        let clients = properties.get('clients').replace(/['"]+/g, '');
        let primary_servers = properties.get('primaryserver').replace(/['"]+/g, '');
        let secondary_servers = properties.get('secondaryserver').replace(/['"]+/g, '');
    
        const isClientExist = clients.split(' ').find((clientItem) => {
            return clientItem === args.client;
        });
        if(!isClientExist) {
            clients = '"' + clients + ' ' + args.client + '"';
            properties.set('clients', clients);
            // const automatePasswordlessClientCmd = config.automate_passwordless_script + ' root ' + args.client + ' ' + args.client_password;
            // logFileStream.write(automatePasswordlessClientCmd + "\n\n");
            // const stdout1 = execSync(automatePasswordlessClientCmd);
            // logFileStream.write(stdout1.toString() + "\n---------------------------\n\n");
        }
    
        const isPrimaryServerExist = primary_servers.split(' ').find((serverItem) => {
            return serverItem === args.server;
        });
        if(!isPrimaryServerExist) {
            primary_servers = '"' + primary_servers + ' ' + args.primary_server + '"';
            properties.set('primaryserver', primary_servers);
            // const automatePasswordlessServerCmd = config.automate_passwordless_script + ' root ' + args.server + ' ' + args.server_password;
            // logFileStream.write(automatePasswordlessServerCmd + "\n\n");
            // const stdout2 = execSync(automatePasswordlessServerCmd);
            // logFileStream.write(stdout2.toString() + "\n---------------------------\n\n");
        }

        const isSecondaryServerExist = secondary_servers.split(' ').find((serverItem) => {
            return serverItem === args.server;
        });
        if(!isSecondaryServerExist) {
            secondary_servers = '"' + secondary_servers + ' ' + args.secondary_server + '"';
            properties.set('secondaryserver', secondary_servers);
            // const automatePasswordlessServerCmd = config.automate_passwordless_script + ' root ' + args.server + ' ' + args.server_password;
            // logFileStream.write(automatePasswordlessServerCmd + "\n\n");
            // const stdout2 = execSync(automatePasswordlessServerCmd);
            // logFileStream.write(stdout2.toString() + "\n---------------------------\n\n");
        }

        await properties.save(config.launch_benchmark_conf_file);
    }

    async initLogger() {
        const managerRegistration = await db.scriptExecutionDatabase().createScriptExecution(info);
        const timestamp = "------------- " + new Date() + " -------------\n"; 
        await fs.writeFile(config.launch_benchmark_log_file, timestamp, () => {});
    }
}

module.exports = {
    scriptExecutionService: function () {
        return new ScriptExecutionService();
    },
};
