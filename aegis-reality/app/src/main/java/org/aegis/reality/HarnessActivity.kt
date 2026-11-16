package org.aegis.reality

import android.app.Activity
import android.os.Bundle

class HarnessActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        finish()
    }
}
