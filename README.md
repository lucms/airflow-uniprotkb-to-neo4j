# Airflow UniProtKB to neo4j

## Setup

1. [Optional, but recommended] Create and activate a [conda env](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) for this solution:

```conda create -n lm-dataeng python=3.9```

```conda activate lm-dataeng```

2. Make sure your current directory is the base folder of this repository.
3. Make sure you have no processes using ports `7474, 7687, 8080`. They must be free for the code to work!
4. Make the `setup.sh` file executable:

```chmod +x setup.sh```

5. Run the setup bash script. It will install all requirements, as well as launch a neo4j database instance and a standalone Airflow instance:

```./setup.sh```

6. Open `http://localhost:7474`, login to the neo4j instance using `user=neo4j` and `password=neo4j`. Will you be prompted to create a new password. Set it to `dataengineering`

> Caution: **the password must be set to `dataengineering`**, otherwise the code won't connect to the database! <br>
> If for some reason you set the password differently, please copy the value you set to the `PASSWORD` variable in `src/dags/con_params.py`

7. Use the Airflow credentials displayed when running `setup.sh` to connect to the airflow instance at `0.0.0.0:8080`.

Now, you are good to go!

## Running the code
1. Open `0.0.0.0:8080` and trigger the `uniprot_xml_to_neo4j` DAG. This should parse all files in the `data` folder (assuming they are all uniprot XML files) and load them into the neo4j database.
2. Enter `http://localhost:7474` to view the neo4j console with extracted uniprot data.

## Extra: running the code for multiple files

To run the code for multiple files, copy the files inside `extra_data` and trigger the Airflow DAG again.

This should load the `Q9Y263.yml` as well as `Q9Y2653.yml` files to the neo4j database!

## Data Model

I've created several classes in Python to abstract the neo4j data model I proposed. This way I can encapsulate the attribute parsing/ relationship creation and create a high level, intuitive interface to work with nodes.

You can find these classes inside `src/dags/nodes`. Good examples are `protein_name.py` and `uniprot_entry.py`

Obs: to handle larger datasets, maybe Node keys should be refactored, in order to assure correct relationships between nodes. But, for simplicity, I've designed them to work at least for the `Q9Y261` entry. 
