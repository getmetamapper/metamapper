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

SNAKE_CASE_SPLIT_TOKENIZER = {
    'type': 'simple_pattern_split',
    'pattern': '_',
}

DBO_NAME_SPLIT_TOKENIZER = {
    'type': 'simple_pattern_split',
    'pattern': '|'.join([
        '\\.',
        ' ',
        '_',
    ])
}

TABLE_INDEX_SETTINGS = {
    'settings': {
        'analysis': {
            'analyzer': {
                'dbo_name_split': {
                    'tokenizer': 'dbo_name_split',
                },
                'custom_english_stop': {
                    'type': 'stop',
                    'stopwords': ENGLISH_STOPWORDS,
                }
            },
            'tokenizer': {
                'dbo_name_split': DBO_NAME_SPLIT_TOKENIZER,
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
            'datastore_engine': {
                'type': 'keyword',
            },
            'name': {
                'type': 'text',
                'analyzer': 'dbo_name_split',
            },
            'exact_name': {
                'type': 'text',
            },
            'description': {
                'type': 'text',
                'analyzer': 'custom_english_stop',
            },
            'schema': {
                'type': 'text',
                'fields': {
                    'keyword': {
                        'type': 'keyword',
                    },
                    'text': {
                        'type': 'text',
                        'analyzer': 'dbo_name_split',
                    }
                }
            },
            'tags': {
                'type': 'text',
                'fields': {
                    'keyword': {
                        'type': 'keyword',
                    },
                    'text': {
                        'type': 'text',
                    }
                }
            },
        }
    }
}


COLUMN_INDEX_SETTINGS = {
    'settings': {
        'analysis': {
            'analyzer': {
                'dbo_name_split': {
                    'tokenizer': 'dbo_name_split',
                },
                'custom_english_stop': {
                    'type': 'stop',
                    'stopwords': ENGLISH_STOPWORDS
                }
            },
            'tokenizer': {
                'dbo_name_split': DBO_NAME_SPLIT_TOKENIZER,
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
            'datastore_engine': {
                'type': 'keyword',
            },
            'table': {
                'type': 'text',
                'analyzer': 'dbo_name_split',
            },
            'name': {
                'type': 'text',
                'analyzer': 'dbo_name_split',
            },
            'exact_name': {
                'type': 'text',
            },
            'description': {
                'type': 'text',
                'analyzer': 'custom_english_stop',
            },
            'schema': {
                'type': 'text',
                'fields': {
                    'keyword': {
                        'type': 'keyword',
                    },
                    'text': {
                        'type': 'text',
                        'analyzer': 'dbo_name_split',
                    }
                }
            },
            'tags': {
                'type': 'text',
                'fields': {
                    'keyword': {
                        'type': 'keyword',
                    },
                    'text': {
                        'type': 'text',
                    }
                }
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
            'datastore_engine': {
                'type': 'keyword',
            },
            'text': {
                'type': 'text',
                'analyzer': 'custom_english_stop',
            }
        }
    }
}
