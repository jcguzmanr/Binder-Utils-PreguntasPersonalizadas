import boto3
from botocore.config import Config
from typing import Tuple, Optional


def make_boto_clients(region: str) -> Tuple[Optional[object], Optional[object]]:
    """
    Crea clientes boto3 para AWS services.
    
    Para el servicio QA solo necesitamos logging (CloudWatch),
    no S3 ni Textract como en el proyecto original.
    
    Args:
        region: Región de AWS
        
    Returns:
        Tuple con (cloudwatch_client, lambda_client)
    """
    try:
        cfg = Config(
            region_name=region,
            read_timeout=25,
            connect_timeout=5,
            retries={"max_attempts": 3, "mode": "standard"},
            max_pool_connections=10,
        )
        
        session = boto3.session.Session(region_name=region)
        
        # Solo clientes necesarios para QA service
        cloudwatch_client = session.client("cloudwatch", config=cfg)
        lambda_client = session.client("lambda", config=cfg)
        
        return cloudwatch_client, lambda_client
        
    except Exception:
        # En modo local o si no hay credenciales AWS, retornar None
        return None, None


def is_aws_environment() -> bool:
    """Verifica si estamos en un entorno AWS (Lambda)"""
    return bool(boto3.Session().get_credentials())
