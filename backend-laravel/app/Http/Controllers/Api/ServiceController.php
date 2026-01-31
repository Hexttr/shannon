<?php

namespace App\Http\Controllers\Api;

use App\Data\Services\CreateServiceData;
use App\Domain\Services\Actions\CreateServiceAction;
use App\Domain\Services\Actions\DeleteServiceAction;
use App\Domain\Services\Actions\GetAllServicesAction;
use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class ServiceController extends Controller
{
    public function __construct(
        private GetAllServicesAction $getAllServicesAction,
        private CreateServiceAction $createServiceAction,
        private DeleteServiceAction $deleteServiceAction
    ) {
    }

    public function index(): JsonResponse
    {
        $services = $this->getAllServicesAction->execute();

        return response()->json([
            'data' => $services->map(fn ($service) => $service->toArray())->values(),
        ]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = CreateServiceData::from($request->all());
        $service = $this->createServiceAction->execute($data);

        return response()->json([
            'data' => $service->toArray(),
        ], 201);
    }

    public function destroy(string $id): JsonResponse
    {
        $this->deleteServiceAction->execute($id);

        return response()->json(null, 204);
    }
}

