<?php

namespace App\Domain\Services\Actions;

use App\Data\Services\CreateServiceData;
use App\Data\Services\ServiceData;
use App\Models\Service;

class CreateServiceAction
{
    public function execute(CreateServiceData $data): ServiceData
    {
        $service = Service::create([
            'name' => $data->name,
            'url' => $data->url,
        ]);

        return ServiceData::from([
            'id' => $service->id,
            'name' => $service->name,
            'url' => $service->url,
            'created_at' => $service->created_at->toISOString(),
            'updated_at' => $service->updated_at->toISOString(),
        ]);
    }
}

