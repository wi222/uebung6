import pulumi
from pulumi_azure_native import web, resources

# Resource Group
resource_group = resources.ResourceGroup('resource_group')

# App Service Plan
plan = web.AppServicePlan('appservice-plan',
    resource_group_name=resource_group.name,
    sku=web.SkuDescriptionArgs(
        name='B1',
        tier='Basic'
    )
)

# Web App
app = web.WebApp('webapp',
    resource_group_name=resource_group.name,
    server_farm_id=plan.id,
    site_config=web.SiteConfigArgs(
        app_settings=[
            web.NameValuePairArgs(
                name='WEBSITE_RUN_FROM_PACKAGE',
                value='1'
            )
        ],
        python_version='3.8'
    )
)

pulumi.export('endpoint', app.default_host_name)