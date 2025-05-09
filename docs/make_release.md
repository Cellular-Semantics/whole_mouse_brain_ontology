# Make a release

## Programmatically edit templates

### Template files and scripts

The main script that drives the template files are located at: `src/scripts/template_generation_tools.py`

Functions to drive templates: 
- `generate_ind_template` -> `src/templates/CCN20230722.tsv`

Generates the named individuals ROBOT template.

- `generate_base_class_template` -> `src/patterns/data/default/CCN20230722_class_base.tsv`

Main DOSDP template file that drives the class generation. This file is merged with the `_class_curation.tsv` at runtime and the final class template is generated. 
Merged template uses the `src/patterns/dosdp-patterns/taxonomy_class.yaml` template. 

- `generate_curated_class_template` -> `src/patterns/data/default/CCN20230722_class_curation.tsv`

This template enables us to do the manual curations without touching the programmatically generated base class template.
This file is not actively used in the current workflow.

- `generate_marker_gene_set_template` -> `src/patterns/data/default/CCN20230722_marker_set.tsv`

Marker set template. Uses the `src/patterns/dosdp-patterns/taxonomy_marker_set.yaml` template.

- `generate_nsforest_marker_gene_set_template` -> `src/patterns/data/default/CCN20230722_nsforest_marker_set.tsv`

NSforest marker set template. Uses the `src/patterns/dosdp-patterns/taxonomy_marker_set.yaml` template.

There are some legacy template functions in the code (such as homology, taxonomy etc.) that are not actively used in the current workflow.

### Regenerate templates

Delete the existing template you want to regenerate and run the following command:

```bash
cd src/dendrograms
make
```
### Run ODK pipeline

```bash
cd src/ontology
sh run.sh make prepare_release
```

## Deploy to local OLS

### Connect to server

- Get SSH keys from the server
Finder>Go>Connect to Server
Enter `smb://files-nfs3/osumi-sutherland` and click `Connect`

Download the contents of the `/servers/172_27_20_150/ssh_keys` folders to your computer in a folder called `ssh_keys`.

_**Note:** files in the `ssh_keys` folder should only be owned by your user (not all users)._

- Make an SSH connection to the server
in the terminal, navigate to the local `ssh_keys` folder and run the following command:
```bash 
ssh -i id_ed25519 ubuntu@172.27.20.150
```

### OLS restart

- In the server navigate to the OLS folder:
```bash
cd  /home/ubuntu/OLS/ols4
```

- Set some env variables:
```bash
export OLS4_CONFIG=./dataload/configs/sanger.json
```

- Shutdown the OLS server
```bash
JAVA_OPTS="-Xms5G -Xmx25G" docker compose down -v
```

- Restart the OLS server (This operation will take approx 10 minutes)
```bash
JAVA_OPTS="-Xms5G -Xmx25G" docker compose up
```


_**Notes:** A fork of the OLS is used for this purpose: https://github.com/hkir-dev/ols4. It customizes the default ports and provides a custom config._

_OLS config located at: https://github.com/hkir-dev/ols4/blob/dev/dataload/configs/sanger.json_

_WMBO ontology is read from (specified in the OLS config): https://github.com/Cellular-Semantics/whole_mouse_brain_ontology/raw/refs/heads/iteration_3/wmbo.owl_

_OLS will be available at: http://172.27.20.150:8081/_