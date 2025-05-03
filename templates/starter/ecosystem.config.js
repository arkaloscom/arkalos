module.exports = {
    apps : [{
        name   : "arkalos-app",
        script : "uv run arkalos serve",
        autorestart: true,
        watch  : false,
    }]
}
