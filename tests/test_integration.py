import pytest
from unittest.mock import patch, MagicMock
from backend.services.scraper import ScraperService

# --- Mock Data for each platform ---

GOOGLE_MAPS_MOCK = [
    {
        'platform': 'google_maps',
        'business_name': 'Islamabad Serena Hotel',
        'website': 'https://www.serenahotels.com/islamabad',
        'phone': '+92 51 111 133 133',
        'address': 'Khayaban-e-Suhrwardy, Islamabad, Pakistan',
        'source_url': 'https://maps.google.com/serena'
    },
    {
        'platform': 'google_maps',
        'business_name': 'The Centaurus Hotel',
        'website': 'https://www.thecentaurus.com/hotel',
        'phone': '+92 51 848 3333',
        'address': 'Jinnah Avenue, Islamabad, Pakistan',
        'source_url': 'https://maps.google.com/centaurus'
    }
]

GOOGLE_SEARCH_MOCK = [
    {
        'platform': 'google_search',
        'business_name': 'Islamabad Serena Hotel', # Cleaned name
        'source_url': 'https://www.serenahotels.com/islamabad'
    },
    {
        'platform': 'google_search',
        'business_name': 'A different hotel with no maps entry',
        'source_url': 'https://www.differenthotel.com'
    }
]

FACEBOOK_MOCK = [
    {
        'platform': 'facebook',
        'business_name': 'Serena Hotel, Islamabad',
        'source_url': 'https://facebook.com/serenahotel',
        'description/snippet': 'The best hotel in town.'
    }
]

LINKEDIN_MOCK = [
     {
        'platform': 'linkedin',
        'business_name': 'The Centaurus Serviced Apartments',
        'source_url': 'https://linkedin.com/company/centaurus-apartments',
        'description/snippet': 'Luxury living.'
    }
]

# Mock the entire orchestrator run
@patch('orchestrator.ScrapeOrchestrator.run')
def test_authoritative_aggregation_and_deduplication(mock_orchestrator_run):
    mock_orchestrator_run.return_value = {
        'query': 'hotels in islamabad',
        'platforms': {
            'google_maps': GOOGLE_MAPS_MOCK,
            'google_search': GOOGLE_SEARCH_MOCK,
            'facebook': FACEBOOK_MOCK,
            'linkedin': LINKEDIN_MOCK,
            'instagram': []
        },
        'errors': [],
        'pagination': {}
    }

    service = ScraperService()
    result = service.run_scraper("hotels in islamabad")

    final_leads = result['platforms']

    assert len(final_leads) == 2

    serena_hotel = next((lead for lead in final_leads if "serena" in lead['business_name'].lower()), None)
    centaurus_hotel = next((lead for lead in final_leads if "centaurus" in lead['business_name'].lower()), None)

    assert serena_hotel is not None
    assert serena_hotel['website'] == 'https://www.serenahotels.com/islamabad'
    assert 'google_maps' in serena_hotel['sources']
    assert 'facebook' in serena_hotel['sources']
    # The Google Search result is for discovery and should be merged if it matches,
    # but since it doesn't add a *new* source URL, we don't assert its presence.
    # The key is that it doesn't create a duplicate entry.

    assert centaurus_hotel is not None
    assert centaurus_hotel['phone'] == '+92 51 848 3333'
    assert 'google_maps' in centaurus_hotel['sources']
    assert 'linkedin' in centaurus_hotel['sources']

    assert "different hotel" not in [lead['business_name'] for lead in final_leads]
