#!/usr/bin/env sh


error () {
    echo "[\033[1;31mError\033[m]" "$@" >&2
}


usage () {
    echo 'Usage:'
    echo '  pack [-h|--help]'
    echo '  pack [-v|--verbose] [-n|--dry] [-d|--delete] [-f|--fmt|--format {fmt}] {source_file/dir}'
    echo ''
    echo 'Optional arguments:'
    echo '  -h, --help      Show this help message and exit.'
    echo '  -v, --verbose   Verbose.'
    echo '  -n, --dry       Print the underlying command and exit.'
    echo '  -d, --delete    Remove source file/dir after packed.'
    echo '  -f {fmt}        Specify the archive format. Default: tar'
    echo ''
    echo 'Supported formats:'

    if command -v tar >/dev/null 2>&1; then
        echo '  tar'
        echo '  tar.bz, tar.bz2, tbz, tbz2'
        echo '  tar.gz, tgz'
    else
        echo '  tar - (not available: tar) (how come?)'
        echo '  tar.bz, tar.bz2, tbz, tbz2 - (not available: tar)'
        echo '  tar.gz, tgz - (not available: tar)'
    fi

    if command -v xz >/dev/null 2>&1; then
        echo '  tar.xz, xz'
    else
        echo '  tar.xz, xz - (not available: xz)'
    fi

    if command -v compress >/dev/null 2>&1; then
        echo '  tar.Z, Z'
    else
        echo '  tar.Z, Z - (not available: compress)'
    fi

    if command -v zip >/dev/null 2>&1; then
        echo '  zip'
    else
        echo '  zip - (not available: zip)'
    fi

    if command -v 7z >/dev/null 2>&1; then
        echo '  7z'
    else
        echo '  7z - (not available: 7z)'
    fi

    echo ''
    echo 'Example:'
    echo '  $ pack -d -f tar my_dir'
}

pack () {
    # Initialize the variables
    dry=0
    clean=0
    fmt='tar'
    verbose=1
    error=''
    source_file=''
    target_file=''

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            ' '*)
                error 'Cannot handle arguments that startswith a space:' "[\033[1;31m$1\033[m]"
                return 1
                ;;
        esac

        if [ "$1" = '-h' ] || [ "$1" = '--help' ]; then
            usage
            return 1

        elif [ "$1" = '-n' ] || [ "$1" = '--dry' ]; then
            dry=1

        elif [ "$1" = '-d' ] || [ "$1" = '--delete' ]; then
            clean=1

        elif [ "$1" = '-v' ] || [ "$1" = '--verbose' ]; then
            verbose=1

        elif [ "$1" = '-f' ] || [ "$1" = '--fmt' ] || [ "$1" = '--format' ]; then
            shift
            fmt="$1"

        else
            case "$1" in
                -*)
                    error "Unknown argument: [\033[1;31m$1\033[m]"
                    usage
                    return 1
                    ;;
                *)
                    if [ "$source_file" = '' ]; then
                        source_file="$1"

                    else
                        error='Only 1 source file/dir is allowed'
                    fi
                    ;;
            esac

        fi

        shift
    done

    # Check if source_file is provided
    if [ -z "$source_file" ]; then
        error='Need to provide source file/dir'

    elif [ ! -e "$source_file" ]; then
        error="File [\033[1;35m$source_file\033[m] does not exist"

    elif [ ! -d "$source_file" ] && [ ! -f "$source_file" ]; then
        error='Only accept file/dir as source file'

    else
        target_file="${source_file}.${fmt}"

        # Check if target_file already exists
        if [ -f "$target_file" ] || [ -d "$target_file" ]; then
            error="[\033[1;35m$target_file\033[m] already exists"
        fi
    fi

    if [ $verbose -ne 0 ]; then
        echo "[verbose] verbose = [\033[1;35m$verbose\033[m]"
        echo "[verbose] dry = [\033[1;35m$dry\033[m]"
        echo "[verbose] clean = [\033[1;35m$clean\033[m]"
        echo "[verbose] fmt = [\033[1;35m$fmt\033[m]"
        echo "[verbose] source_file = [\033[1;35m$source_file\033[m]"
        echo "[verbose] target_file = [\033[1;35m$target_file\033[m]"
    fi

    if [ -n "$error" ]; then
        error "$error"
        return 1
    fi

    # Normalize fmt (destructive)
    case "$fmt" in
        tar)      fmt='tar' ;;
        tar.bz)   fmt='tar.bz2' ;;
        tbz)      fmt='tar.bz2' ;;
        tar.bz2)  fmt='tar.bz2' ;;
        tbz2)     fmt='tar.bz2' ;;
        bz)       fmt='tar.bz2' ;;
        bz2)      fmt='tar.bz2' ;;
        tar.gz)   fmt='tar.gz' ;;
        tgz)      fmt='tar.gz' ;;
        gz)       fmt='tar.gz' ;;
        tar.xz)   fmt='tar.xz' ;;
        xz)       fmt='xz' ;;
        tar.Z)    fmt='tar.Z' ;;
        Z)        fmt='Z' ;;
        zip)      fmt='zip' ;;
        7z)       fmt='7z' ;;
        *)
            error "Unsupported archive format: [\033[1;35m${fmt}\033[m]"
            return 1
            ;;
    esac

    # Supportability check
    case "$fmt" in
        tar | tar.*)
            if ! command -v tar >/dev/null 2>&1; then
                error "Unsupported archive format: [$fmt] (need tar)"
                return 1
            fi
            ;;
    esac

    case "$fmt" in
        tar.xz | xz)
            if ! command -v xz >/dev/null 2>&1; then
                error "Unsupported archive format: [$fmt] (need xz)"
                return 1
            fi

            if [ "$fmt" = 'xz' ] && [ -d "$source_file" ]; then
                error "Format [xz] doesn't work on directory"
                return 1
            fi
            ;;

        tar.Z | Z)
            if ! command -v compress >/dev/null 2>&1; then
                error "Unsupported archive format: [$fmt] (need compress)"
                return 1
            fi

            if [ "$fmt" = 'Z' ] && [ -d "$source_file" ]; then
                error "Format [Z] doesn't work on directory"
                return 1
            fi
            ;;

        zip | 7z)
            if ! command -v "$fmt" >/dev/null 2>&1; then
                error "Unsupported archive format: [$fmt] (need $fmt)"
                return 1
            fi
            ;;
    esac

    if [ $dry -eq 0 ]; then
        dry_cmd=''
    else
        dry_cmd='echo [dry]'
    fi

    # Archive
    case "$fmt" in
        tar)
            $dry_cmd tar cvf  "$target_file" --exclude "$target_file" "$source_file"
            ret_code=$?
            ;;

        tar.bz2)
            $dry_cmd tar jcvf  "$target_file" --exclude "$target_file" "$source_file"
            ret_code=$?
            ;;

        tar.gz)
            $dry_cmd tar zcvf "$target_file" --exclude "$target_file" "$source_file"
            ret_code=$?
            ;;

        tar.xz)
            middle_file="_$source_file.tar"

            $dry_cmd tar cvf "$middle_file" --exclude "$middle_file" "$source_file" && \
                $dry_cmd xz "$middle_file"
            ret_code=$?
            ;;

        xz)
            # ``xz`` automatically removes the original file
            if [ $clean -eq 0 ]; then
                keep_arg='--keep'
            else
                keep_arg=''
            fi

            $dry_cmd xz $keep_arg "$source_file"
            ret_code=$?
            ;;

        tar.Z)
            middle_file="_$source_file.tar"

            $dry_cmd tar cvf "$middle_file" --exclude "$middle_file" "$source_file" && \
                $dry_cmd compress "$middle_file"
            ret_code=$?
            ;;

        Z)
            if [ $clean -eq 0 ]; then
                middle_file="_pack_tmp_$source_file"
                $dry_cmd cp "$source_file" "$middle_file" && \
                    $dry_cmd compress "$middle_file" && \
                    mv "$middle_file.Z" "$source_file.Z"
                ret_code=$?
            else
                $dry_cmd compress "$source_file"
                ret_code=$?
            fi
            ;;

        *)
            error "Unsupported archive format: [\033[1;35m${fmt}\033[m]"
            return 1
            ;;
    esac

    if [ $ret_code -ne 0 ]; then
        return $ret_code
    fi

    if [ $clean -eq 1 ]; then
        if [ -f "$source_file" ]; then
            $dry_cmd rm "$source_file"
        elif [ -d "$source_file" ]; then
            $dry_cmd rm -r "$source_file"
        fi
        ret_code=$?
    fi

    echo '[Debug exit]'
    return $ret_code

    # format check based on the file extension
    case "$afile" in
        -)          afile='-'; format='tar' ;;
        *.tar)      format='tar' ;;
        *.tar.bz)   afile="${afile%*.tar.bz}.tar.bz2" ; format='tar.bz2' ;;
        *.tbz)      afile="${afile%*.tar.bz}.tbz2" ;    format='tar.bz2' ;;
        *.tar.bz2)  format='tar.bz2' ;;
        *.tbz2)     format='tar.bz2' ;;
        *.tar.gz)   format='tar.gz' ;;
        *.tgz)      format='tar.gz' ;;
        *.tar.xz)   afile="${afile%*.tar.xz}.tar" ;     format='tar.xz' ;;
        *.xz)       afile="${afile%*.xz}.tar" ;         format='tar.xz' ;;
        *.tar.Z)    afile="${afile%*.tar.Z}.tar" ;      format='tar.Z' ;;
        *.Z)        afile="${afile%*.Z}.tar" ;          format='tar.Z' ;;
        *.bz)       afile="${afile%*.bz}.tar.bz2" ;     format='tar.bz2' ;;
        *.bz2)      afile="${afile%*.bz2}.tar.bz2" ;    format='tar.bz2' ;;
        *.gz)       afile="${afile%*.gz}.tar.gz" ;      format='tar.gz' ;;
        *.zip)      format='zip' ;;
        *.7z)       format='7z' ;;
        *)
            echo "Don't know how to pack \"$afile\""
            unset afile
            unset format
            unset clean
            return 1
            ;;
    esac

    # need "zip", check if "zip" installed
    if [ "$format" = 'zip' ] && ! command -v zip >/dev/null 2>&1; then
        echo 'The "zip" utility is not installed'
        unset afile
        unset format
        unset clean
        return 1
    fi

    # need "7z", check if "7z" installed
    if [ "$format" = '7z' ] && ! command -v 7z >/dev/null 2>&1; then
        echo 'The "7z" utility is not installed'
        unset afile
        unset format
        unset clean
        return 1
    fi

    # "7z" format streaming is not supported
    if [ "$format" = '7z' ] && [ "$afile" = '-' ]; then
        echo '"7z" format streaming is not supported'
        unset afile
        unset format
        unset clean
        return 1
    fi

    # packing
    case "$format" in
        tar)        tar cvf  "$afile" --exclude "$afile" "$@" ;;
        tar.bz2)    tar jcvf "$afile" --exclude "$afile" "$@" ;;
        tar.gz)     tar zcvf "$afile" --exclude "$afile" "$@" ;;
        tar.xz)
            if [ "$afile" = '-' ]; then
                tar cvf - --exclude "$afile" "$@" | xz --stdout
            else
                # ``xz`` automatically removes the original file
                tar cvf "$afile" --exclude "$afile" "$@" && xz "$afile"
            fi
            ;;
        tar.Z)
            # ``compress`` automatically removes the original file
            if [ "$afile" = '-' ]; then
                tar cvf "$afile" "$@" | compress -c -
            else
                tar cvf "$afile" --exclude "$afile" "$@" && compress -f "$afile"
            fi
            ;;
        zip)    zip --symlinks --exclude "$afile" -r "$afile" "$@" ;;
        7z)     7z a "$afile" "$@" ;;
    esac

    ret_code=$?

    # check if packing succeed
    if [ ${ret_code} -ne 0 ]; then
        unset afile
        unset format
        unset clean
        return 1
    fi

    # clean up source files if clean bit is set
    if [ ${ret_code} -eq 0 ] && [ "$clean" -eq 1 ]; then
        while [ $# -gt 0 ]; do
            if [ "$1" != "$afile" ]; then
                rm -r "$1"
            fi
            shift
        done
    fi

    unset afile
    unset format
    unset clean
    return 0
}


pack "$@"
