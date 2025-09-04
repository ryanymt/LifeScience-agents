# drug-discovery_agent/drug_discovery_agent/specialists/compound_analyzer/tools/get_smiles.py
# Copyright 2025 Google LLC
# ... (add license header)

"""Tool for finding a compound's SMILES string from its name using PubChem."""

import pubchempy as pcp

def get_smiles_from_name(compound_name: str) -> str:
    """
    Looks up a compound's SMILES string by its name in the PubChem database.

    Args:
        compound_name: The common or IUPAC name of the compound.

    Returns:
        The canonical SMILES string for the compound, or an error message.
    """
    try:
        # Search PubChem by name
        compounds = pcp.get_compounds(compound_name, 'name')
        if not compounds:
            return f"No compound found in PubChem for name: '{compound_name}'"

        # Take the first and most likely result
        compound = compounds[0]
        
        # Return its isomeric SMILES string
        smiles = compound.isomeric_smiles
        if smiles:
            return f"The SMILES string for '{compound_name}' is {smiles}"
        else:
            return f"Could not find a SMILES string for '{compound_name}'"

    except Exception as e:
        return f"An error occurred while querying PubChem for the name '{compound_name}': {e}"
