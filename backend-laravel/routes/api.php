<?php

use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\PentestController;
use App\Http\Controllers\Api\ServiceController;
use Illuminate\Support\Facades\Route;

Route::prefix('auth')->group(function () {
    Route::post('/login', [AuthController::class, 'login']);
    Route::middleware('auth:sanctum')->group(function () {
        Route::get('/me', [AuthController::class, 'me']);
    });
});

Route::middleware('auth:sanctum')->group(function () {
    Route::apiResource('services', ServiceController::class);
    Route::apiResource('pentests', PentestController::class);
    Route::post('pentests/{id}/start', [PentestController::class, 'start']);
    Route::post('pentests/{id}/stop', [PentestController::class, 'stop']);
    Route::get('pentests/{pentestId}/vulnerabilities', [\App\Http\Controllers\Api\VulnerabilityController::class, 'index']);
    Route::get('pentests/{pentestId}/logs', [\App\Http\Controllers\Api\LogController::class, 'index']);
});

