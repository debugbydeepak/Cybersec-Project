import functools
import logging

logger = logging.getLogger(__name__)

# A registry to hold all the plugins that have been plugged in.
PLUGIN_REGISTRY = {}

def secureway_plugin(name: str, version: str = "1.0", category: str = "security_rule"):
    """
    Unified Plugin System Decorator.
    Allows for modular extension of the SECUREWAY engine by plugging
    specific security rules into the CI/CD pipeline.
    """
    def decorator(func):
        PLUGIN_REGISTRY[name] = {
            "version": version,
            "category": category,
            "func": func
        }
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"[Plugin: {name} v{version}] Executing rule...")
            result = func(*args, **kwargs)
            logger.info(f"[Plugin: {name} v{version}] Execution complete. Result: {result}")
            return result
        return wrapper
    return decorator

def execute_plugins(*args, **kwargs):
    """
    Execute all registered plugins and collect their results.
    """
    results = {}
    for name, plugin_meta in PLUGIN_REGISTRY.items():
        func = plugin_meta["func"]
        try:
            res = func(*args, **kwargs)
            results[name] = {"status": "success", "result": res}
        except Exception as e:
            results[name] = {"status": "error", "message": str(e)}
    return results
