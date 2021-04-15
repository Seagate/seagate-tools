#Perfpro_deployment

##Pre-Requisites in order to run Perfpro_deployment :
1. Verify 'hosts' file is empty in "inventories/perfpro_deployment/" directory (~/seagate-tools/performance/perfPro-deployment/inventories/perfpro_deployment/).  
2. Update config.yml with valid information of SUT and build in order to run this.

## Example how to run 
ansible-playbook perfpro_deploy.yml -i inventories/perfpro_deployment/hosts --ask-vault-pass -v
