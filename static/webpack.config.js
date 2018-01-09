/*
 * webpack.config.js
 */

const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')
const glob = require('glob')
const webpack = require('webpack')
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const chalk = require('chalk')

const env = {
  'process.env': {
    NODE_ENV: JSON.stringify(process.env.NODE_ENV || 'development'),
    BUILD: JSON.stringify(new Date().toLocaleString()),
  }
}

const isProduction = process.env.NODE_ENV === 'production'

const babelOptions = {
  presets: ['env'],
  plugins: [
    'transform-object-rest-spread'
  ]
}

const extractStyle = new ExtractTextPlugin({
  filename: '[name].css',
  disable: false /* !isProduction */,
})

const entries = {
  donors:  ['./js/donors.js'],
  import:  ['./js/import.js'],
  navbar:  ['./js/navbar.js'],
  samples: ['./js/samples.js'],
  users:   ['./js/users.js'],
}

module.exports = {
  entry: entries,

  devtool: isProduction ? 'source-map' : 'cheap-module-source-map',

  module: {
    rules:
    [
      {
        test: /\.js$/,
        loader: 'babel-loader',
        options: babelOptions,
      },
      {
        test: /\.css$/,
        use: extractStyle.extract({
          fallback: 'style-loader',
          use: ['css-loader', 'postcss-loader']
        })
      },
      {
        test: /\.(jpe?g|png|gif|svg|woff2)$/i,
        use: [
          'url-loader'
        ]
      }
    ]
  },

  plugins: [
    new webpack.DefinePlugin(env),
    extractStyle,
    /*new webpack.optimize.CommonsChunkPlugin({
       name: ['common']
     }),*/

  ],

  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'dist')
  },

  watchOptions: {
    ignored: [
      'node_modules',
      'dist',
    ]
  }
};

function copyFiles(source, dest) {
  const apply = compiler => {
    compiler.plugin('done', (compilation) => {
      console.log(chalk.bold(`Moving files from ${chalk.blue(source)} to ${chalk.blue(dest)}`))
      fs.readdirSync(source).forEach(file => {
        const sourceFile = join(source, file)
        const destFile = join(dest, file)
        const content = fs.readFileSync(sourceFile)
        fs.writeFileSync(destFile, content)
      })
    })
  }

  return { apply }
}

function exec(command) {
  const apply = compiler => {
    compiler.plugin('done', (compilation) => {
      console.log(chalk.bold(`Executing ${chalk.blue(command)}`))
      execSync(command)
    })
  }

  return { apply }
}

function execBefore(command) {
  const apply = compiler => {
    compiler.plugin('run', (compilation, cb) => {
      console.log(chalk.bold(`Executing ${chalk.blue(command)}`))
      execSync(command)

      cb()
    })
  }

  return { apply }
}

function removeFiles(pattern, before = true) {
  const apply = compiler => {
    compiler.plugin(before ? 'run' : 'emit', (compilation, cb) => {
      glob.sync(pattern).forEach(file => {
        console.log(`Removing ${chalk.red.bold(file)}`)
        fs.unlinkSync(file)
      })

      cb()
    })
  }

  return { apply }
}
