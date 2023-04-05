pip install -r requirements.txt
docker run \
  -d \
  --publish=7474:7474 --publish=7687:7687 \
  --volume=`pwd`/neo4j/data:/data \
  neo4j:latest

export AIRFLOW__CORE__DAGS_FOLDER=`pwd`/src/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=false

airflow standalone