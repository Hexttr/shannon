<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('vulnerabilities', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('pentest_id')->constrained()->onDelete('cascade');
            $table->string('title');
            $table->text('description');
            $table->string('severity'); // critical, high, medium, low
            $table->string('cvss_score')->nullable();
            $table->string('cve')->nullable();
            $table->text('solution')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('vulnerabilities');
    }
};

