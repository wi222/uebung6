import pulumi
import os
import shutil
from pulumi_azure_native import resources, storage, web, insights
from pulumi import FileAsset

# ZIP-Datei der Anwendung erstellen
zip_file_path = 'webapp.zip'

# Löschen der vorhandenen ZIP-Datei, falls vorhanden
if os.path.exists(zip_file_path):
    os.remove(zip_file_path)

# ZIP-Datei der Anwendung erstellen
if os.path.exists('clco-demo'):
    shutil.make_archive('webapp', 'zip', 'clco-demo')
    print(f"ZIP-Datei '{zip_file_path}' wurde erfolgreich erstellt.")
else:
    raise FileNotFoundError("Das Verzeichnis 'clco-demo' wurde nicht gefunden.")

# Überprüfen, ob die ZIP-Datei erstellt wurde und nicht leer ist
if os.path.exists(zip_file_path) and os.path.getsize(zip_file_path) > 0:
    print(f"ZIP-Datei '{zip_file_path}' wurde erfolgreich erstellt und ist nicht leer.")
else:
    raise FileNotFoundError("Die ZIP-Datei wurde nicht erstellt oder ist leer.")

# Erstellen einer Ressourcengruppe
resource_group = resources.ResourceGroup("uebung4-resourcegroup", location="canadacentral")

# Erstellen eines Storage-Accounts
storage_account = storage.StorageAccount("storageaccount",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    sku=storage.SkuArgs(name="Standard_LRS"),
    kind="StorageV2",
    allow_blob_public_access=True
)

# Erstellen eines Blob-Containers
blob_container = storage.BlobContainer("blobcontainer",
    account_name=storage_account.name,
    resource_group_name=resource_group.name,
    public_access="Blob"
)

# Hochladen einer Datei in den Blob-Container
app_blob = storage.Blob("webappzip",
    resource_group_name=resource_group.name,
    account_name=storage_account.name,
    container_name=blob_container.name,
    source=FileAsset(zip_file_path)
)

# Generieren der Blob-URL
blob_url = pulumi.Output.concat("https://", storage_account.name, ".blob.core.windows.net/", blob_container.name, "/", app_blob.name)

# Erstellen eines App Service Plans
app_service_plan = web.AppServicePlan("serviceplan",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    kind="Linux",
    reserved=True,
    sku=web.SkuDescriptionArgs(
        tier="Standard",
        name="S1",
    )
)

# Application Insights erstellen
app_insights = insights.Component("appinsights",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    application_type="web",
    kind="web",
    ingestion_mode="ApplicationInsights"
)

# Erstellen einer Web-App
web_app = web.WebApp("webapp",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    server_farm_id=app_service_plan.id,
    site_config=web.SiteConfigArgs(
        app_settings=[
            web.NameValuePairArgs(name="WEBSITE_RUN_FROM_PACKAGE", value=blob_url),
            web.NameValuePairArgs(name="APPINSIGHTS_INSTRUMENTATIONKEY", value=app_insights.instrumentation_key),
        ],
        linux_fx_version="PYTHON|3.11",
    )
)

# Outputs exportieren
pulumi.export("web_app_url", web_app.default_host_name)