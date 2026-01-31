<?php

namespace App\Domain\Auth\Actions;

use App\Data\Auth\UserData;
use Illuminate\Contracts\Auth\Authenticatable;

class GetCurrentUserAction
{
    public function execute(Authenticatable $user): UserData
    {
        return UserData::from($user);
    }
}

