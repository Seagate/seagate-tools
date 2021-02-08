module.exports = {
  outputDir: "web-dist",
  devServer: {
    proxy: "http://localhost:6786"
  },
  configureWebpack: {
    devtool: "source-map"
  }
};
