settings = {"title": "API", "hide_top_bar": True}
template = {
    "swagger": "2.0",
    "hide_top_bar": True,
    "info": {
        "title": "M API",
        # "description": "API for my data",
        "contact": {
            "responsibleOrganization": "ME",
            "responsibleDeveloper": "Me",
            "email": "xxx@",
            "url": "www.",
        },
        "termsOfService": "#",
        "version": "2.0.X",
    },
    "host": "",  # overrides localhost:500
    "basePath": "/apiv2",  # base bash for blueprint registration
    "schemes": ["http", "https"],
}
