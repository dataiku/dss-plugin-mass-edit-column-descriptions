import dataiku
from dataiku.runnables import Runnable
import json

class MyRunnable(Runnable):
    def __init__(self, project_key, config, plugin_config):
        self.config = config
        self.renamings = json.loads(config["descriptions"])
        
    def get_progress_target(self):
        return None

    def run(self, progress_callback):
        project = dataiku.api_client().get_default_project()
        
        if self.config["all_datasets"]:
            datasets_to_consider = [d["name"] for d in project.list_datasets()]
        else:
            datasets_to_consider = [d.strip() for d in self.config["dataset_names"].split("\n")]
        
        for dataset_name in datasets_to_consider:
            dataset = project.get_dataset(dataset_name)
            settings = dataset.get_settings()
            print("Considering dataset: %s" % dataset.name)
            
            changed = False
            for column in settings.schema_columns:
                new_description = self.renamings.get(column["name"], None)
                if new_description is None:
                    continue
                if column.get("comment") is not None and not self.config["override"]:
                    continue
                column["comment"] = new_description
                print("Changed column %s of dataset %s" % (column["name"], dataset.name))
                changed = True
        
            if changed:
                settings.save()
        