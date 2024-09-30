const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CaseSensitivePathsPlugin = require('case-sensitive-paths-webpack-plugin');
module.exports = {
  entry: "./src/index.js",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "bundle.js",
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        exclude: /node_modules/,
        use: ["babel-loader"],
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader", 'postcss-loader'],
      },
    ],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"), // 将 @ 映射到 src 文件夹
      '@components': path.resolve(__dirname, 'src/components'), // 将 @components 映射到 src/components 文件夹
      '@ui': path.resolve(__dirname, 'src/components/ui'), // 将 @ui 映射到 src/components/ui 文件夹
    },
    extensions: [".ts", ".tsx", ".js", ".jsx", ".*"],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: "./public/index.html",
    }),
    new CaseSensitivePathsPlugin(), // 确保路径大小写正确
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, "public"),
    },
    port: 3000,
  },
};
