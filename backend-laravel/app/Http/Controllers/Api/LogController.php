<?php

namespace App\Http\Controllers\Api;

use App\Domain\Logs\Actions\GetLogsByPentestAction;
use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;

class LogController extends Controller
{
    public function __construct(
        private GetLogsByPentestAction $getLogsAction
    ) {
    }

    public function index(string $pentestId): JsonResponse
    {
        $logs = $this->getLogsAction->execute($pentestId);

        return response()->json([
            'data' => $logs->map(fn ($log) => $log->toArray())->values(),
        ]);
    }
}

