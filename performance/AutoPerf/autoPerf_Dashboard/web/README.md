# Hardware Allocation API

POSTMAN Link for API -- https://www.getpostman.com/collections/b5b5e178653b253b6e13

# Deploy using PM2

## Start command
- Create PM2 single instance
  - ```npm run pm2```
  - ```npm run pm2-restart```
- Create PM2 processes.json
  - ```npm run pm2-cluster```
  - ```npm run pm2-cluster-restart```
- Manually
 -  ```pm2 start npm --name "hw-api" -- run start:production```