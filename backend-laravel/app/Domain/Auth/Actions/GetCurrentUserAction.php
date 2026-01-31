<?php

namespace App\Domain\Auth\Actions;

use App\Data\Auth\UserData;
use Illuminate\Contracts\Auth\Authenticatable;

class GetCurrentUserAction
{
    public function execute(Authenticatable $user): UserData
    {
        return UserData::from([
            'id' => $user->id,
            'username' => $user->username,
            'email' => $user->email,
            'created_at' => $user->created_at?->toISOString(),
            'updated_at' => $user->updated_at?->toISOString(),
        ]);
    }
}

