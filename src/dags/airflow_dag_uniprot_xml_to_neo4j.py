from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from datetime import timedelta
from uniprot_xml_to_neo4j import batch_uniprot_xml_to_neo4j
import os


DEFAULT_ARGS = {
    'owner': 'Lucas Miura',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['luc.ms22@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

DAG_NAME = 'uniprot_xml_to_neo4j'

# Parametrize number of parallel batches and ideal batch size,
# in order to optimize writes to the database.
NUM_PARALLEL_BATCHES = 2
IDEAL_BATCH_SIZE = 100
PARALLEL_BATCH_OPERATOR_NAMES = [
    f'batch_xml_to_neo4j_{num}' for num in range(NUM_PARALLEL_BATCHES)
]

# Get the absolute path of the current directory
current_dir = os.path.abspath(os.getcwd())

# Get the absolute path of the target folder
data_dir = os.path.join(os.path.abspath(current_dir), 'data')

uniprot_files = [
    os.path.join(data_dir, f) 
    for f in os.listdir(data_dir) 
    if os.path.isfile(os.path.join(data_dir, f))
]


def split(a, n):
    """
    splits an iterable into n chunks and returns a list of these chunks
    """
    k, m = divmod(len(a), n)
    return [a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]


def create_chunks(**kwargs):
    num_files = len(uniprot_files)

    if num_files > NUM_PARALLEL_BATCHES*IDEAL_BATCH_SIZE:
        print('Alert:: operating over ideal batch size capacity. Slower performance expected')
    
    # Separate batches and push them to XCOM
    chunks = split(uniprot_files, NUM_PARALLEL_BATCHES)

    return {
        PARALLEL_BATCH_OPERATOR_NAMES[num] : chunks[num]
        for num in range(NUM_PARALLEL_BATCHES)
    }


def parse_chunk(**kwargs):
    task_id = kwargs['task_instance'].task_id
    chunks = kwargs['ti'].xcom_pull(task_ids='create_chunks')

    chunk = chunks[task_id]

    if len(chunk) > 0:
        batch_uniprot_xml_to_neo4j(chunk)


with DAG(DAG_NAME, "catchup=False", default_args=DEFAULT_ARGS,
         schedule=None) as dag:
    
    # Create file chunks
    create_batches_operator = PythonOperator(
        task_id='create_chunks',
        python_callable=create_chunks,
        trigger_rule='all_success'
    )

    # Parallelize batch processing to improve performance
    parallel_batch_operators = [
        PythonOperator(
            task_id=PARALLEL_BATCH_OPERATOR_NAMES[num],
            python_callable=parse_chunk,
            trigger_rule='all_success'
        )
        for num in range(NUM_PARALLEL_BATCHES)
    ]

    for batch_operator in parallel_batch_operators:
        batch_operator.set_upstream(create_batches_operator)
