"""
Patent Data Ingestion Module

This module handles the ingestion and processing of patent data from various sources,
including government patent databases, API endpoints, and file uploads.
"""

import asyncio
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime
import httpx
from google.cloud import bigquery
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class PatentIngestor:
    """Main class for patent data ingestion and processing"""
    
    def __init__(self):
        self.bigquery_client = None
        self.dataset_id = os.getenv('BIGQUERY_DATASET_ID')
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        
        # Initialize BigQuery client if credentials are available
        if self.project_id:
            try:
                self.bigquery_client = bigquery.Client(project=self.project_id)
                print(f"BigQuery client initialized for project: {self.project_id}")
            except Exception as e:
                print(f"Warning: Could not initialize BigQuery client: {e}")
    
    async def ingest_from_api(self, api_url: str, headers: Dict = None) -> List[Dict]:
        """
        Ingest patent data from an API endpoint
        
        Args:
            api_url: URL of the patent API
            headers: Optional headers for the API request
            
        Returns:
            List of patent dictionaries
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, headers=headers or {})
                response.raise_for_status()
                
                data = response.json()
                print(f"Successfully ingested {len(data)} patents from API")
                return data
                
        except Exception as e:
            print(f"Error ingesting from API: {e}")
            return []
    
    def ingest_from_csv(self, file_path: Union[str, Path]) -> List[Dict]:
        """
        Ingest patent data from CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of patent dictionaries
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            
            patents = []
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                patents = list(reader)
            
            print(f"Successfully ingested {len(patents)} patents from CSV")
            return patents
            
        except Exception as e:
            print(f"Error ingesting from CSV: {e}")
            return []
    
    def ingest_from_json(self, file_path: Union[str, Path]) -> List[Dict]:
        """
        Ingest patent data from JSON file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of patent dictionaries
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"JSON file not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
            
            # Handle both single dict and list of dicts
            if isinstance(data, dict):
                patents = [data]
            elif isinstance(data, list):
                patents = data
            else:
                raise ValueError("JSON must contain a dictionary or list of dictionaries")
            
            print(f"Successfully ingested {len(patents)} patents from JSON")
            return patents
            
        except Exception as e:
            print(f"Error ingesting from JSON: {e}")
            return []
    
    def clean_patent_data(self, patents: List[Dict]) -> List[Dict]:
        """
        Clean and standardize patent data
        
        Args:
            patents: List of raw patent dictionaries
            
        Returns:
            List of cleaned patent dictionaries
        """
        cleaned_patents = []
        
        for patent in patents:
            try:
                cleaned_patent = {
                    'id': patent.get('id', '').strip(),
                    'title': patent.get('title', '').strip(),
                    'abstract': patent.get('abstract', '').strip(),
                    'inventors': self._clean_inventors(patent.get('inventors', [])),
                    'assignee': patent.get('assignee', '').strip(),
                    'publication_date': self._clean_date(patent.get('publication_date')),
                    'patent_number': patent.get('patent_number', '').strip(),
                    'classification_codes': patent.get('classification_codes', []),
                    'claims': patent.get('claims', []),
                    'ingested_at': datetime.utcnow().isoformat()
                }
                
                # Only add patents with minimum required fields
                if cleaned_patent['id'] and cleaned_patent['title']:
                    cleaned_patents.append(cleaned_patent)
                else:
                    print(f"Skipping patent with missing required fields: {patent}")
                    
            except Exception as e:
                print(f"Error cleaning patent data: {e}, Patent: {patent}")
                continue
        
        print(f"Cleaned {len(cleaned_patents)} patents out of {len(patents)} raw patents")
        return cleaned_patents
    
    def _clean_inventors(self, inventors) -> List[str]:
        """Clean and standardize inventor names"""
        if isinstance(inventors, str):
            inventors = [inventors]
        elif not isinstance(inventors, list):
            return []
        
        return [inv.strip() for inv in inventors if inv and inv.strip()]
    
    def _clean_date(self, date_value) -> Optional[str]:
        """Clean and standardize dates"""
        if not date_value:
            return None
        
        try:
            # Try to parse various date formats
            if isinstance(date_value, str):
                # Remove any extra whitespace
                date_value = date_value.strip()
                
                # Try parsing common formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                    try:
                        parsed_date = datetime.strptime(date_value, fmt)
                        return parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
            
            return str(date_value)
            
        except Exception:
            return None
    
    def save_to_bigquery(self, patents: List[Dict], table_name: str = 'patents') -> bool:
        """
        Save patent data to BigQuery
        
        Args:
            patents: List of patent dictionaries
            table_name: Name of the BigQuery table
            
        Returns:
            True if successful, False otherwise
        """
        if not self.bigquery_client or not self.dataset_id:
            print("BigQuery client not configured. Skipping BigQuery save.")
            return False
        
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(patents)
            
            # Load data to BigQuery
            job = self.bigquery_client.load_table_from_dataframe(
                df, table_id, 
                job_config=bigquery.LoadJobConfig(
                    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                    schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
                )
            )
            
            job.result()  # Wait for the job to complete
            print(f"Successfully saved {len(patents)} patents to BigQuery table: {table_id}")
            return True
            
        except Exception as e:
            print(f"Error saving to BigQuery: {e}")
            return False
    
    def save_to_json(self, patents: List[Dict], file_path: Union[str, Path]) -> bool:
        """
        Save patent data to JSON file
        
        Args:
            patents: List of patent dictionaries
            file_path: Path where to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(patents, jsonfile, indent=2, ensure_ascii=False)
            
            print(f"Successfully saved {len(patents)} patents to JSON: {file_path}")
            return True
            
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False

# Utility functions
async def ingest_patent_batch(
    sources: List[Dict],
    output_format: str = 'json',
    output_path: Optional[str] = None
) -> List[Dict]:
    """
    Ingest patent data from multiple sources and save to specified format
    
    Args:
        sources: List of source dictionaries with 'type' and 'path' or 'url'
        output_format: 'json', 'bigquery', or 'both'
        output_path: Path for JSON output (if applicable)
        
    Returns:
        List of all ingested and cleaned patents
    """
    ingestor = PatentIngestor()
    all_patents = []
    
    for source in sources:
        source_type = source.get('type')
        source_path = source.get('path') or source.get('url')
        
        print(f"Processing source: {source_type} - {source_path}")
        
        if source_type == 'csv':
            patents = ingestor.ingest_from_csv(source_path)
        elif source_type == 'json':
            patents = ingestor.ingest_from_json(source_path)
        elif source_type == 'api':
            patents = await ingestor.ingest_from_api(source_path, source.get('headers'))
        else:
            print(f"Unknown source type: {source_type}")
            continue
        
        # Clean the patent data
        cleaned_patents = ingestor.clean_patent_data(patents)
        all_patents.extend(cleaned_patents)
    
    print(f"Total patents ingested: {len(all_patents)}")
    
    # Save based on output format
    if output_format in ['json', 'both'] and output_path:
        ingestor.save_to_json(all_patents, output_path)
    
    if output_format in ['bigquery', 'both']:
        ingestor.save_to_bigquery(all_patents)
    
    return all_patents

if __name__ == "__main__":
    # Example usage
    async def main():
        sources = [
            {
                'type': 'json',
                'path': 'data/sample_patents.json'
            }
        ]
        
        patents = await ingest_patent_batch(
            sources=sources,
            output_format='json',
            output_path='output/processed_patents.json'
        )
        
        print(f"Ingestion complete. Processed {len(patents)} patents.")
    
    # Run the example
    # asyncio.run(main())