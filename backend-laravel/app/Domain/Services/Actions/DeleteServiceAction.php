<?php

namespace App\Domain\Services\Actions;

use App\Models\Service;

class DeleteServiceAction
{
    public function execute(string $id): void
    {
        $service = Service::findOrFail($id);
        $service->delete();
    }
}

