plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "org.aegis.reality"
    compileSdk = 37

    defaultConfig {
        applicationId = "org.aegis.reality"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    androidTestImplementation("androidx.test:runner:1.7.0")
    androidTestImplementation("androidx.test:rules:1.7.0")
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.junit)
}
