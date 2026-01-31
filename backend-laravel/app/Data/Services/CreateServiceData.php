<?php

namespace App\Data\Services;

use Spatie\LaravelData\Data;

class CreateServiceData extends Data
{
    public function __construct(
        public string $name,
        public string $url,
    ) {
    }
}

