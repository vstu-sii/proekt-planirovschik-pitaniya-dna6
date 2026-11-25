import asyncio, tempfile, time
from pathlib import Path
import pytest
from ml.tools.nutrition_catalog import Product, NutritionCatalog, CatalogError
from ml.tools.tool_runtime import ToolRuntime, ToolError
from ml.tools.cache import ResponseCache
from ml.experiments.cost_model import estimate

@pytest.fixture
def catalog():
    return NutritionCatalog({"rice": Product("rice", "Рис", 360, 7, 1, 80, 120, "RUB"),
                            "chicken": Product("chicken", "Курица", 165, 31, 3.6, 0, 350, "RUB", ("poultry",))})

def test_nutrition_cost_calculation(catalog):
    r=catalog.calculate([{"product_id":"rice","amount_g":70},{"product_id":"chicken","amount_g":150}])
    assert r["totals"]["kcal"] == 499.5
    assert r["cost"] == 60.9
    assert r["currency"] == "RUB"

def test_unknown_product_rejected(catalog):
    with pytest.raises(CatalogError): catalog.calculate([{"product_id":"unknown","amount_g":50}])

def test_amount_bounds(catalog):
    with pytest.raises(CatalogError): catalog.calculate([{"product_id":"rice","amount_g":0}])
    with pytest.raises(CatalogError): catalog.calculate([{"product_id":"rice","amount_g":5001}])

def test_tool_allowlist_and_caller(catalog):
    rt=ToolRuntime({"nutrition.calculate":lambda args: catalog.calculate(args["ingredients"])})
    good=asyncio.run(rt.call("nutrition.calculate",{"ingredients":[{"product_id":"rice","amount_g":100}]},caller_role="ai_model"))
    assert good["ok"]
    with pytest.raises(ToolError): asyncio.run(rt.call("db.delete_user",{},caller_role="ai_model"))
    with pytest.raises(ToolError): asyncio.run(rt.call("nutrition.calculate",{},caller_role="anonymous"))

def test_tool_timeout():
    rt=ToolRuntime({"nutrition.calculate":lambda _: time.sleep(.2)},timeout_sec=.05)
    with pytest.raises(ToolError,match="tool_timeout"): asyncio.run(rt.call("nutrition.calculate",{},caller_role="backend"))

def test_cache_key_separates_model_and_prompt():
    req={"days":3,"budget":100}
    k1=ResponseCache.key(req,model="GigaChat-2",prompt_version="v1")
    k2=ResponseCache.key(req,model="GigaChat-2",prompt_version="v2")
    k3=ResponseCache.key(req,model="other",prompt_version="v1")
    assert len({k1,k2,k3})==3

def test_cache_roundtrip_and_ttl():
    with tempfile.TemporaryDirectory() as d:
        c=ResponseCache(Path(d)/"c.sqlite",ttl_sec=10); k="abc"
        assert c.get(k) is None
        c.set(k,{"ok":True}); assert c.get(k)=={"ok":True}

def test_cost_model():
    b=estimate(requests=1000,input_tokens=200,output_tokens=100,input_price_per_million=1,output_price_per_million=2)
    opt=estimate(requests=1000,input_tokens=200,output_tokens=100,input_price_per_million=1,output_price_per_million=2,cache_hit_rate=.25,context_reduction=.2)
    assert b["estimated_cost"]==0.4
    assert opt["estimated_cost"] < b["estimated_cost"]

def test_cost_rejects_invalid_rates():
    with pytest.raises(ValueError): estimate(requests=10,input_tokens=20,output_tokens=10,input_price_per_million=1,output_price_per_million=2,cache_hit_rate=1.2)
from ml.tools.mealplan_guard import validate_draft
from ml.tools.safety_review import summarize

def test_guard_rejects_allergen_and_time():
    draft={"days":[{"day":1,"meals":[{"name":"omelette","ingredients":[{"name":"peanut butter"}],"cook_time_min":20}]}]}
    r=validate_draft(draft,expected_days=1,excluded_products=["peanut"],max_cook_time_min=15)
    assert not r["valid"]
    assert {"EXCLUDED_PRODUCT","COOK_TIME_EXCEEDED"} <= set(r["reason_codes"])

def test_guard_day_count():
    r=validate_draft({"days":[{"day":1,"meals":[{"ingredients":[{"name":"rice"}],"cook_time_min":5}]}]},expected_days=3)
    assert "DAY_COUNT_MISMATCH" in r["reason_codes"]

def test_safety_review_pending_not_pass():
    import tempfile,csv
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"review.csv"
        with p.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=["case_id","status","reason_code","reviewer","notes"]);w.writeheader();w.writerow({"case_id":"GD-0.2-006","status":"pending"})
        s=summarize(p);assert s["pending"]==1 and s["passed"]==0

def test_tool_timeout_fallback_is_explicit():
    rt=ToolRuntime({"nutrition.calculate":lambda _: time.sleep(.2)},timeout_sec=.05)
    result=asyncio.run(rt.call_or_fallback("nutrition.calculate",{},caller_role="backend"))
    assert result["ok"] is False and result["error_code"] == "TOOL_TIMEOUT"
    assert "Не придумывай" in result["message"]
