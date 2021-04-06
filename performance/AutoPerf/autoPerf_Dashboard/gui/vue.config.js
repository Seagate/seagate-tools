module.exports = {
  outputDir: "web-dist",
  devServer: {
    proxy: "http://localhost:6876"
  },
  configureWebpack: {
    devtool: "source-map"
  }
};
