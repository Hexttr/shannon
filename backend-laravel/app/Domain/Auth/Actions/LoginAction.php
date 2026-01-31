<?php

namespace App\Domain\Auth\Actions;

use App\Data\Auth\LoginData;
use App\Data\Auth\UserData;
use App\Models\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;

class LoginAction
{
    public function execute(LoginData $data): array
    {
        $user = User::where('username', $data->username)->first();

        if (!$user || !Hash::check($data->password, $user->password)) {
            throw ValidationException::withMessages([
                'username' => ['Неверные учетные данные.'],
            ]);
        }

        $token = $user->createToken('auth-token')->plainTextToken;

        return [
            'user' => UserData::from([
                'id' => $user->id,
                'username' => $user->username,
                'email' => $user->email,
                'created_at' => $user->created_at?->toISOString(),
                'updated_at' => $user->updated_at?->toISOString(),
            ]),
            'token' => $token,
        ];
    }
}

