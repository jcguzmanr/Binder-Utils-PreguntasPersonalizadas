import json
import sys
import logging
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Formatter que convierte logs a JSON estructurado"""
    
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        # Agregar campos adicionales si existen
        if hasattr(record, 'event'):
            log_entry["event"] = record.event
        if hasattr(record, 'id'):
            log_entry["id"] = record.id
        if hasattr(record, 'err'):
            log_entry["error"] = record.err
        if hasattr(record, 'status'):
            log_entry["status"] = record.status
        if hasattr(record, 'ms'):
            log_entry["duration_ms"] = record.ms
            
        # Agregar cualquier campo extra
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'event', 'id', 
                          'err', 'status', 'ms']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class AppLogger:
    """Logger personalizado para la aplicación QA"""
    
    def __init__(self, json_logs: bool = True, level: str = "INFO"):
        self.logger = logging.getLogger("qa-service")
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Limpiar handlers existentes
        self.logger.handlers.clear()
        
        # Configurar handler
        handler = logging.StreamHandler(sys.stdout)
        
        if json_logs:
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
        
        self.logger.addHandler(handler)
    
    def event(self, event: str, **kwargs):
        """Log un evento con contexto adicional"""
        # Crear un record personalizado
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, __file__, 0, 
            event, (), None
        )
        
        # Agregar campos adicionales
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        self.logger.handle(record)
    
    def info(self, message: str, **kwargs):
        """Log info con contexto adicional"""
        self.event(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error con contexto adicional"""
        record = self.logger.makeRecord(
            self.logger.name, logging.ERROR, __file__, 0, 
            message, (), None
        )
        
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        self.logger.handle(record)
    
    def warning(self, message: str, **kwargs):
        """Log warning con contexto adicional"""
        record = self.logger.makeRecord(
            self.logger.name, logging.WARNING, __file__, 0, 
            message, (), None
        )
        
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        self.logger.handle(record)


def get_app_logger(json_logs: bool = True, level: str = "INFO") -> AppLogger:
    """Factory para obtener logger de la aplicación"""
    return AppLogger(json_logs=json_logs, level=level)
