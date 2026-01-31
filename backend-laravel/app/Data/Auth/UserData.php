<?php

namespace App\Data\Auth;

use Spatie\LaravelData\Data;

class UserData extends Data
{
    public function __construct(
        public string $id,
        public string $username,
        public string $email,
        public ?string $created_at = null,
        public ?string $updated_at = null,
    ) {
    }
}

