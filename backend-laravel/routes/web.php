<?php

use Illuminate\Support\Facades\Route;

// Пустой маршрут login для предотвращения ошибки "Route [login] not defined"
Route::get('/login', function () {
    return redirect('/');
})->name('login');

Route::get('/', function () {
    return response()->json(['message' => 'Shannon API']);
});


