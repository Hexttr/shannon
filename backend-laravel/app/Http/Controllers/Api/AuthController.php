<?php

namespace App\Http\Controllers\Api;

use App\Data\Auth\LoginData;
use App\Domain\Auth\Actions\GetCurrentUserAction;
use App\Domain\Auth\Actions\LoginAction;
use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class AuthController extends Controller
{
    public function __construct(
        private LoginAction $loginAction,
        private GetCurrentUserAction $getCurrentUserAction
    ) {
    }

    public function login(Request $request): JsonResponse
    {
        $data = LoginData::from($request->all());
        $result = $this->loginAction->execute($data);

        return response()->json([
            'user' => $result['user']->toArray(),
            'token' => $result['token'],
        ]);
    }

    public function me(): JsonResponse
    {
        $user = $this->getCurrentUserAction->execute(Auth::user());

        return response()->json($user->toArray());
    }
}

