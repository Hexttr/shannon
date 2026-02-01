<?php

return [
    'claude' => [
        'api_key' => env('CLAUDE_API_KEY'),
    ],

    'ollama' => [
        'api_url' => env('OLLAMA_API_URL', 'http://localhost:11434/api'),
        'model' => env('OLLAMA_MODEL', 'llama3.2:3b'),
    ],

    'ssh' => [
        'host' => env('SSH_HOST', 'localhost'),
        'username' => env('SSH_USERNAME', 'root'),
        'password' => env('SSH_PASSWORD'),
    ],

    'pusher' => [
        'app_id' => env('PUSHER_APP_ID'),
        'key' => env('PUSHER_APP_KEY'),
        'secret' => env('PUSHER_APP_SECRET'),
        'cluster' => env('PUSHER_APP_CLUSTER'),
    ],
];


