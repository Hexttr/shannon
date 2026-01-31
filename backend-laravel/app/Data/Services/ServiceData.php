<?php

namespace App\Data\Services;

use Spatie\LaravelData\Data;

class ServiceData extends Data
{
    public function __construct(
        public string $id,
        public string $name,
        public string $url,
        public string $created_at,
        public string $updated_at,
    ) {
    }
}

