const CracoAntDesignPlugin = require("craco-antd");
const path = require("path");

module.exports = {
    plugins: [
        {
            plugin: CracoAntDesignPlugin,
            options: {
                customizeTheme: {
                  "@primary-color": "#f7777b",
                  "@link-color": "#f7777b",
                  "@primary-color": "#f7777b",
                  "@error-color": "#faad14",
                  "@success-color": "#52c41a",
                }
            }
        }
    ]
};
