cmake_minimum_required(VERSION 3.20)
project(FilesystemUFS1 VERSION 1.0.0 LANGUAGES C)
include(CTest)
include(FetchContent)
find_package(OpenSSL REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(INFILTRATR_COMMON_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(INFILTRATR_COMMON_BUILD_SHARED OFF CACHE BOOL "" FORCE)
FetchContent_Declare(infiltratr_common
 GIT_REPOSITORY https://github.com/Infiltrator-Projects/Libraries.git
 GIT_TAG 5b5fb95988c8d0b53ed29fdecfb0b70274182fd6)
FetchContent_MakeAvailable(infiltratr_common)
# Common is linked into the filesystem; its development files are not installed.
set_property(DIRECTORY "${infiltratr_common_SOURCE_DIR}" PROPERTY EXCLUDE_FROM_ALL TRUE)
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/version.h" "#define LD_VERSION \"1.0.0\"\n")
add_library(ufs1-driver SHARED
 native/ufs_native.c native/ufs_worker.c
 compat/legacy_services.c compat/runtime_alloc.c
 module/ufs_module.c)
set_source_files_properties(native/ufs_worker.c PROPERTIES
 COMPILE_DEFINITIONS "main=ifs_ufs_worker_main")
set_target_properties(ufs1-driver PROPERTIES PREFIX "" OUTPUT_NAME "UFS1" SUFFIX ".so")
target_compile_definitions(ufs1-driver PRIVATE _GNU_SOURCE _FILE_OFFSET_BITS=64 IFS_UFS_MAJOR=1)
target_compile_options(ufs1-driver PRIVATE -Wall -Wextra -Wpedantic -Werror)
target_link_options(ufs1-driver PRIVATE -Wl,-z,defs)
target_include_directories(ufs1-driver PRIVATE
 "${CMAKE_CURRENT_SOURCE_DIR}/native" "${CMAKE_CURRENT_SOURCE_DIR}/compat"
 "${CMAKE_CURRENT_SOURCE_DIR}/include" "${CMAKE_CURRENT_BINARY_DIR}")
target_link_libraries(ufs1-driver PRIVATE InfiltratrCommon::Common OpenSSL::Crypto)
if(BUILD_TESTING)
 add_executable(ufs1-module-test tests/test_module.c)
 target_include_directories(ufs1-module-test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/include")
 target_link_libraries(ufs1-module-test PRIVATE ufs1-driver)
 add_test(NAME ufs1-module-interface COMMAND ufs1-module-test)
endif()
install(TARGETS ufs1-driver LIBRARY DESTINATION /System/Filesystems)

# Build the same current, source-derived manual used by native installer release.
set(UFS1_GENERATED_PDF "${CMAKE_CURRENT_BINARY_DIR}/Filesystem-UFS1.pdf")
add_custom_command(
 OUTPUT "${UFS1_GENERATED_PDF}"
 COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/standalone/generate_manual.py"
         "${CMAKE_CURRENT_SOURCE_DIR}/VERSION"
         "${CMAKE_CURRENT_SOURCE_DIR}/docs/UFS1.pages"
         "${UFS1_GENERATED_PDF}"
 DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/VERSION"
         "${CMAKE_CURRENT_SOURCE_DIR}/docs/UFS1.pages"
         "${CMAKE_CURRENT_SOURCE_DIR}/standalone/manual.py"
         "${CMAKE_CURRENT_SOURCE_DIR}/standalone/generate_manual.py"
 VERBATIM)
add_custom_target(ufs1-manual ALL DEPENDS "${UFS1_GENERATED_PDF}")
install(FILES "${UFS1_GENERATED_PDF}"
        DESTINATION /System/Resources/Documentation)
