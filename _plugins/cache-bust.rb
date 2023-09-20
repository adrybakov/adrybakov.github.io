# Copyright (c) 2022 Maruan Al-Shedivat.

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# based on https://distresssignal.org/busting-css-cache-with-jekyll-md5-hash
# https://gist.github.com/BryanSchuetz/2ee8c115096d7dd98f294362f6a667db
module Jekyll
    module CacheBust
        class CacheDigester
            require 'digest/md5'
            require 'pathname'

            attr_accessor :file_name, :directory

            def initialize(file_name:, directory: nil)
                self.file_name = file_name
                self.directory = directory
            end

            def digest!
                [file_name, '?', Digest::MD5.hexdigest(file_contents)].join
            end

            private

            def directory_files_content
                target_path = File.join(directory, '**', '*')
                Dir[target_path].map{|f| File.read(f) unless File.directory?(f) }.join
            end

            def file_content
                local_file_name = file_name.slice((file_name.index('assets/')..-1))
                File.read(local_file_name)
            end

            def file_contents
                is_directory? ? file_content : directory_files_content
            end

            def is_directory?
                directory.nil?
            end
        end

        def bust_file_cache(file_name)
            CacheDigester.new(file_name: file_name, directory: nil).digest!
        end

        def bust_css_cache(file_name)
            CacheDigester.new(file_name: file_name, directory: 'assets/_sass').digest!
        end
    end
end

Liquid::Template.register_filter(Jekyll::CacheBust)
