# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tool for identifying a compound from its SMILES string using PubChem."""

import pubchempy as pcp

def get_compound_info(smiles_string: str) -> str:
    """
    Looks up a compound by its SMILES string in PubChem.

    Args:
        smiles_string: The SMILES string representation of the drug.

    Returns:
        A string with the compound's name and other details, or an error message.
    """
    try:
        # Search PubChem by SMILES string
        compounds = pcp.get_compounds(smiles_string, 'smiles')
        if not compounds:
            return f"No compound found in PubChem for SMILES: {smiles_string}"

        # Take the first and most likely result
        compound = compounds[0]

        # Prioritize synonyms to find the common drug name. 
        # Added this after a test as PubMed use common name mostly
        common_name = "N/A"
        if compound.synonyms:
            # The first synonym is often the most common name (e.g., 'Olaparib').
            common_name = compound.synonyms[0]

        iupac_name = compound.iupac_name or "N/A"
        formula = compound.molecular_formula or "N/A"

        # If the best we found was the IUPAC name, reflect that.
        if common_name == "N/A":
            common_name = iupac_name

        return (
            f"Successfully identified compound from SMILES '{smiles_string}':\n"
            f"- Common Name: {common_name}\n"
            f"- IUPAC Name: {iupac_name}\n"
            f"- Molecular Formula: {formula}"
        )

    except Exception as e:
        return f"An error occurred while querying PubChem: {e}"