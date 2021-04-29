const config = require('../../../../config');
const statusCode = require('../../../../common/statusCode');
const message = require('../../../../common/message');
const propertiesReader = require('properties-reader');
const fs = require('fs');
const { SocketService } = require('../../../../services/websocket/socket-service');

class MetadataService {
    /**
     * 
     */
    async getDefaultParameters() {
        try {
            const properties = propertiesReader(config.launch_benchmark_conf_file);
            const benchmarks = properties.get('benchmarks').replace(/['"]+/g, '');
            const operations = properties.get('operations').replace(/['"]+/g, '');
            const templates = properties.get('templates').replace(/['"]+/g, '');
            const configurations = properties.get('configurations').replace(/['"]+/g, '');
            const clients = properties.get('clients').replace(/['"]+/g, '');
            const primary_servers = properties.get('primaryserver').replace(/['"]+/g, '');
            const secondary_servers = properties.get('secondaryserver').replace(/['"]+/g, '');
            const sampling = properties.get('sampling').replace(/['"]+/g, '');

            return {
                statusCode: statusCode.success,
                message: "",
                data: {
                    benchmarks: benchmarks.split(' '),
                    operations: operations.split(' '),
                    templates: templates.split(' '),
                    configurations: configurations.split(' '),
                    clients: clients.split(' '),
                    primary_servers: primary_servers.split(' '),
                    secondary_servers: secondary_servers.split(' '),
                    sampling: sampling.split(' ')
                }
            };
        } catch (error) {
            throw {
                statusCode: error.statusCode,
                message: error.message,
                data: JSON.stringify(error),
            };
        }
    }

    /**
     * 
     */
    async getScriptLastExecLog() {
        setInterval(function () {
            console.log("Sending message");
            SocketService.sendMessage("Hello");
        }, 1000);
        try {
            // const log = fs.readFileSync(config.launch_benchmark_log_file, { encoding: "utf8", flag: "r" });
            return {
                statusCode: statusCode.success,
                message: "",
                data: "Getting message",
            };
        } catch (error) {
            return error;
        }
    }

    async addNode(gid, node) {
        try {
            const properties = propertiesReader(config.launch_benchmark_conf_file);
            let nodes = properties.get('primaryserver').replace(/['"]+/g, '');
            const isNodeExist = nodes.split(' ').includes(node);
            
            if(!isNodeExist) {
                nodes = `"${nodes} ${node}"`;
                properties.set('primaryserver', nodes);
                await properties.save(config.launch_benchmark_conf_file);
            }

            return {
                statusCode: statusCode.created,
                message: "Node added successfully."
            };
        } catch (error) {
            throw {
                statusCode: error.statusCode,
                message: error.message,
                data: JSON.stringify(error),
            };
        }
    }

    async addClient(gid, client) {
        try {
            const properties = propertiesReader(config.launch_benchmark_conf_file);
            let clients = properties.get('clients').replace(/['"]+/g, '');
            const isClientExist = clients.split(' ').includes(client);
            
            if(!isClientExist) {
                clients = `"${clients} ${client}"`;
                properties.set('clients', clients);
                await properties.save(config.launch_benchmark_conf_file);
            }

            return {
                statusCode: statusCode.created,
                message: "Client added successfully."
            };
        } catch (error) {
            throw {
                statusCode: error.statusCode,
                message: error.message,
                data: JSON.stringify(error),
            };
        }
    }
}

module.exports = {
    metadataService: function () {
        return new MetadataService();
    },
};
