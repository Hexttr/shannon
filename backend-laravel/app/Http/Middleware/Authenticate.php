<?php

namespace App\Http\Middleware;

use Illuminate\Auth\Middleware\Authenticate as Middleware;
use Illuminate\Http\Request;

class Authenticate extends Middleware
{
    /**
     * Get the path the user should be redirected to when they are not authenticated.
     */
    protected function redirectTo(Request $request): ?string
    {
        // Для API запросов всегда возвращаем null (будет JSON ответ)
        if ($request->expectsJson() || $request->is('api/*')) {
            return null;
        }
        
        // Для веб-запросов пытаемся редиректить на login (если маршрут существует)
        try {
            return route('login');
        } catch (\Exception $e) {
            // Если маршрут login не существует, возвращаем null
            return null;
        }
    }
}


