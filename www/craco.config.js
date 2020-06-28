const CracoAntDesignPlugin = require("craco-antd");
const path = require("path");

module.exports = {
    plugins: [
        {
            plugin: CracoAntDesignPlugin,
            options: {
                customizeTheme: {
                  "@primary-color": "#1890ff",
                  "@link-color": "#1890ff"
                }
            }
        }
    ]
};
