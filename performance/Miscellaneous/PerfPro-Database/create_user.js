db.createUser(
{
user: "perfpro",
pwd: "PerfPro",
roles: [
{ role: "readWrite", db: "performance_db"}
]}
)

