<?php

namespace App\Domain\Services\Actions;

use App\Data\Services\ServiceData;
use App\Models\Service;
use Illuminate\Support\Collection;

class GetAllServicesAction
{
    /**
     * @return Collection<int, ServiceData>
     */
    public function execute(): Collection
    {
        return Service::all()->map(fn (Service $service) => ServiceData::from([
            'id' => $service->id,
            'name' => $service->name,
            'url' => $service->url,
            'created_at' => $service->created_at->toISOString(),
            'updated_at' => $service->updated_at->toISOString(),
        ]));
    }
}

