<?php

namespace App\Data\Logs;

use Spatie\LaravelData\Data;

class LogData extends Data
{
    public function __construct(
        public string $id,
        public string $pentest_id,
        public string $level,
        public string $message,
        public string $timestamp,
    ) {
    }
}

