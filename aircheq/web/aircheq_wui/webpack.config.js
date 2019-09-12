var path = require("path");

const isProduction = process.env.NODE_ENV === "production";

var babelOptions = {
  presets: [
    "react",
    [
      "es2015",
      {
        modules: false
      }
    ]
  ]
};

function tsModule() {
  return {
    rules: [
      {
        test: /\.ts(x?)$/,
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
            options: babelOptions
          },
          {
            loader: "ts-loader"
            //options: {compilerOptions:{sourceMap: !isProduction}}
          }
        ]
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
            options: babelOptions
          }
        ]
      }
    ]
  };
}

module.exports = {
  mode: "development",
  entry: {
    main: "./src/index.tsx"
  },
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "bundle.js"
  },
  devServer: {
    publicPath: "/dist/",
    proxy: {
      "/api/*": {
        target: "http://localhost:5000"
      }
    },
    port: 3000,
    inline: true
  },
  resolve: {
    extensions: [".ts", ".tsx", ".js"]
  },
  module: tsModule()
};
