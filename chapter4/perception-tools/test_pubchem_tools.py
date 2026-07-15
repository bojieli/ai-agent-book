"""
Real API tests for PubChem tools.
These tests make actual API calls to PubChem to verify functionality.
"""
import asyncio
import json
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pubchem_tools import (
    search_compounds,
    get_compound_properties,
    get_compound_synonyms,
    search_similar_compounds
)


class TestPubChemSearch:
    """Tests for compound search functionality."""
    
    @pytest.mark.asyncio
    async def test_search_by_name(self):
        """Test searching compounds by name."""
        result = await search_compounds(
            query="aspirin",
            search_type="name",
            max_results=5
        )
        
        # Parse result
        data = json.loads(result.text)
        assert data["success"] is True
        
        message = data["message"]
        assert message["query"] == "aspirin"
        assert message["search_type"] == "name"
        assert len(message["compounds"]) > 0
        
        # Check first compound has expected fields
        compound = message["compounds"][0]
        assert compound["cid"] is not None
        assert compound["name"] is not None
        assert compound["molecular_formula"] is not None
        assert compound["molecular_weight"] is not None
        
        print(f"✅ Found {len(message['compounds'])} compounds for 'aspirin'")
        print(f"   First: {compound['name']} (CID: {compound['cid']})")
    
    @pytest.mark.asyncio
    async def test_search_by_cid(self):
        """Test searching compound by CID."""
        result = await search_compounds(
            query="2244",  # Aspirin CID
            search_type="cid",
            max_results=1
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        message = data["message"]
        assert len(message["compounds"]) == 1
        
        compound = message["compounds"][0]
        assert compound["cid"] == 2244
        assert "aspirin" in compound["name"].lower() or "acetylsalicylic" in compound["name"].lower()
        
        print(f"✅ Found compound by CID: {compound['name']}")
    
    @pytest.mark.asyncio
    async def test_search_by_formula(self):
        """Test searching compounds by molecular formula."""
        result = await search_compounds(
            query="C9H8O4",  # Aspirin formula
            search_type="formula",
            max_results=10
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        message = data["message"]
        assert len(message["compounds"]) > 0
        
        # Check all compounds have the correct formula
        for compound in message["compounds"]:
            assert compound["molecular_formula"] == "C9H8O4"
        
        print(f"✅ Found {len(message['compounds'])} compounds with formula C9H8O4")
    
    @pytest.mark.asyncio
    async def test_search_by_smiles(self):
        """Test searching compound by SMILES."""
        result = await search_compounds(
            query="CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin SMILES
            search_type="smiles",
            max_results=1
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        message = data["message"]
        assert len(message["compounds"]) > 0
        
        print(f"✅ Found compound by SMILES")
    
    @pytest.mark.asyncio
    async def test_search_invalid_query(self):
        """Test searching with invalid query."""
        result = await search_compounds(
            query="",
            search_type="name",
            max_results=5
        )
        
        data = json.loads(result.text)
        assert data["success"] is False
        assert "required" in data["message"].lower()
        
        print("✅ Correctly handled invalid query")
    
    @pytest.mark.asyncio
    async def test_search_not_found(self):
        """Test searching for non-existent compound."""
        result = await search_compounds(
            query="xyzabc123notarealcompound999",
            search_type="name",
            max_results=5
        )
        
        data = json.loads(result.text)
        # Should fail or return empty results
        if data["success"]:
            assert data["message"]["count"] == 0
        
        print("✅ Handled non-existent compound search")


class TestPubChemProperties:
    """Tests for compound properties functionality."""
    
    @pytest.mark.asyncio
    async def test_get_properties(self):
        """Test getting compound properties."""
        result = await get_compound_properties(
            cid=2244,  # Aspirin
            properties=["MolecularWeight", "MolecularFormula", "XLogP", "TPSA"]
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        message = data["message"]
        assert message["cid"] == 2244
        
        props = message["properties"]
        assert "MolecularWeight" in props
        assert "MolecularFormula" in props
        assert props["MolecularFormula"] == "C9H8O4"
        
        print(f"✅ Retrieved properties for aspirin:")
        print(f"   Formula: {props['MolecularFormula']}")
        print(f"   Weight: {props['MolecularWeight']}")
    
    @pytest.mark.asyncio
    async def test_get_default_properties(self):
        """Test getting default properties."""
        result = await get_compound_properties(
            cid=2244  # Aspirin
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        props = data["message"]["properties"]
        # Should have default properties
        assert len(props) > 0
        assert "MolecularWeight" in props
        
        print(f"✅ Retrieved {len(props)} default properties")
    
    @pytest.mark.asyncio
    async def test_get_properties_invalid_cid(self):
        """Test getting properties with invalid CID."""
        result = await get_compound_properties(
            cid=-1
        )
        
        data = json.loads(result.text)
        assert data["success"] is False
        
        print("✅ Correctly handled invalid CID")


class TestPubChemSynonyms:
    """Tests for compound synonyms functionality."""
    
    @pytest.mark.asyncio
    async def test_get_synonyms(self):
        """Test getting compound synonyms."""
        result = await get_compound_synonyms(
            cid=2244,  # Aspirin
            max_synonyms=10
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        message = data["message"]
        assert message["cid"] == 2244
        assert len(message["synonyms"]) > 0
        
        # Check that common names are included
        synonyms_lower = [s.lower() for s in message["synonyms"]]
        assert any("aspirin" in s for s in synonyms_lower)
        
        print(f"✅ Retrieved {len(message['synonyms'])} synonyms:")
        print(f"   Examples: {', '.join(message['synonyms'][:3])}")
    
    @pytest.mark.asyncio
    async def test_get_synonyms_limit(self):
        """Test synonym count limit."""
        result = await get_compound_synonyms(
            cid=2244,
            max_synonyms=5
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        synonyms = data["message"]["synonyms"]
        assert len(synonyms) <= 5
        
        print(f"✅ Correctly limited synonyms to {len(synonyms)}")


class TestPubChemSimilarity:
    """Tests for similar compounds search."""
    
    @pytest.mark.asyncio
    async def test_search_similar(self):
        """Test searching similar compounds."""
        result = await search_similar_compounds(
            cid=2244,  # Aspirin
            similarity_threshold=0.9,
            max_results=5
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        message = data["message"]
        assert message["reference_cid"] == 2244
        assert message["similarity_threshold"] == 0.9
        
        similar = message["similar_compounds"]
        # Should find at least some similar compounds
        if len(similar) > 0:
            compound = similar[0]
            assert compound["cid"] is not None
            assert compound["cid"] != 2244  # Should not include itself
            assert compound["name"] is not None
            
            print(f"✅ Found {len(similar)} similar compounds:")
            print(f"   Example: {compound['name']} (CID: {compound['cid']})")
        else:
            print("✅ Search completed (no similar compounds at 0.9 threshold)")
    
    @pytest.mark.asyncio
    async def test_search_similar_lower_threshold(self):
        """Test searching similar compounds with lower threshold."""
        result = await search_similar_compounds(
            cid=2244,
            similarity_threshold=0.7,  # Lower threshold
            max_results=10
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        similar = data["message"]["similar_compounds"]
        # With lower threshold, should find more compounds
        print(f"✅ Found {len(similar)} compounds at 0.7 similarity")


class TestPubChemRateLimit:
    """Tests for rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_multiple_requests(self):
        """Test that multiple requests are rate-limited."""
        import time
        
        start_time = time.time()
        
        # Make 5 requests in quick succession
        for i in range(5):
            result = await search_compounds(
                query="aspirin",
                search_type="name",
                max_results=1
            )
            data = json.loads(result.text)
            assert data["success"] is True
        
        elapsed = time.time() - start_time
        
        # Should take at least 0.8 seconds (5 requests * 0.2s delay - 0.2s for first)
        assert elapsed >= 0.8
        
        print(f"✅ Rate limiting working: {elapsed:.2f}s for 5 requests")


# Run tests
if __name__ == "__main__":
    print("=" * 70)
    print("Running PubChem Tools Real API Tests")
    print("=" * 70)
    print()
    
    # Run with pytest
    pytest.main([__file__, "-v", "-s"])
