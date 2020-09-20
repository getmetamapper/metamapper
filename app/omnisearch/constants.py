ENGLISH_STOPWORDS = [
    'i',
    'me',
    'my',
    'myself',
    'we',
    'our',
    'ours',
    'ourselves',
    'you',
    'your',
    'yours',
    'yourself',
    'yourselves',
    'he',
    'him',
    'his',
    'himself',
    'she',
    'her',
    'hers',
    'herself',
    'it',
    'its',
    'itself',
    'they',
    'them',
    'their',
    'theirs',
    'themselves',
    'what',
    'which',
    'who',
    'whom',
    'this',
    'that',
    'these',
    'those',
    'am',
    'is',
    'are',
    'was',
    'were',
    'be',
    'been',
    'being',
    'have',
    'has',
    'had',
    'having',
    'do',
    'does',
    'did',
    'doing',
    'a',
    'an',
    'the',
    'and',
    'but',
    'if',
    'or',
    'because',
    'as',
    'until',
    'while',
    'of',
    'at',
    'by',
    'for',
    'with',
    'about',
    'against',
    'between',
    'into',
    'through',
    'during',
    'before',
    'after',
    'above',
    'below',
    'to',
    'from',
    'up',
    'down',
    'in',
    'out',
    'on',
    'off',
    'over',
    'under',
    'again',
    'further',
    'then',
    'once',
    'here',
    'there',
    'when',
    'where',
    'why',
    'how',
    'all',
    'any',
    'both',
    'each',
    'few',
    'more',
    'most',
    'other',
    'some',
    'such',
    'no',
    'nor',
    'not',
    'only',
    'own',
    'same',
    'so',
    'than',
    'too',
    'very',
    's',
    't',
    'can',
    'will',
    'just',
    'don',
    'should',
    'now'
]


TABLE_INDEX_SETTINGS = {
    'settings': {
        'analysis': {
            'analyzer': {
                'slug_case_split': {
                    'tokenizer': 'slug_case_split',
                },
                'custom_english_stop': {
                    'type': 'stop',
                    'stopwords': ENGLISH_STOPWORDS
                }
            },
            'tokenizer': {
                'slug_case_split': {
                    'type': 'simple_pattern_split',
                    'pattern': '_',
                }
            }
        }
    },
    'mappings': {
        'properties': {
            'pk': {
                'type': 'keyword',
            },
            'workspace_id': {
                'type': 'keyword',
            },
            'datastore_id': {
                'type': 'keyword',
            },
            'datastore': {
                'type': 'text',
                'analyzer': 'slug_case_split',
            },
            'schema': {
                'type': 'text',
                'analyzer': 'slug_case_split',
            },
            'name': {
                'type': 'text',
                'analyzer': 'slug_case_split',
            },
            'description': {
                'type': 'text',
                'analyzer': 'custom_english_stop',
            },
        }
    }
}


COLUMN_INDEX_SETTINGS = {
    'settings': {
        'analysis': {
            'analyzer': {
                'slug_case_split': {
                    'tokenizer': 'slug_case_split',
                },
                'custom_english_stop': {
                    'type': 'stop',
                    'stopwords': ENGLISH_STOPWORDS
                }
            },
            'tokenizer': {
                'slug_case_split': {
                    'type': 'simple_pattern_split',
                    'pattern': '_',
                }
            }
        }
    },
    'mappings': {
        'properties': {
            'pk': {
                'type': 'keyword'
            },
            'workspace_id': {
                'type': 'keyword'
            },
            'datastore_id': {
                'type': 'keyword'
            },
            'datastore': {
                'type': 'text',
                'analyzer': 'slug_case_split',
            },
            'schema': {
                'type': 'text',
                'analyzer': 'slug_case_split',
            },
            'table': {
                'type': 'text',
                'analyzer': 'slug_case_split',
            },
            'name': {
                'type': 'text',
                'analyzer': 'slug_case_split',
            },
            'description': {
                'type': 'text',
                'analyzer': 'custom_english_stop',
            },
        }
    }
}


COMMENT_INDEX_SETTINGS = {
    'settings': {
        'analysis': {
            'analyzer': {
                'custom_english_stop': {
                    'type': 'stop',
                    'stopwords': ENGLISH_STOPWORDS
                }
            }
        }
    },
    'mappings': {
        'properties': {
            'pk': {
                'type': 'keyword',
            },
            'workspace_id': {
                'type': 'keyword',
            },
            'datastore_id': {
                'type': 'keyword',
            },
            'text': {
                'type': 'text',
                'analyzer': 'custom_english_stop',
            }
        }
    }
}
